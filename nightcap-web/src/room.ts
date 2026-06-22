export interface RoomMember {
  client_id: string;
  participant_id: string;
  role: "host" | "player" | "display";
  joined_at: string;
}

export interface RoomJoinRequest {
  session_id: string;
  client_id: string;
  participant_id: string;
  role: RoomMember["role"];
}

export interface RoomSnapshot {
  session_id: string | null;
  room_id: string;
  member_count: number;
  members: RoomMember[];
  updated_at: string;
}

export interface RoomActionResponse {
  ok: true;
  snapshot: RoomSnapshot;
}

export interface NightcapRoomEnv {
  ARCWRIGHT_API_BASE_URL: string;
}

export class NightcapRoom extends DurableObject {
  private readonly roomId: string;
  private currentSessionId: string | null = null;
  private readonly members = new Map<string, RoomMember>();

  constructor(state: DurableObjectState, env: NightcapRoomEnv) {
    super(state, env);
    this.roomId = state.id.toString();
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname.endsWith("/snapshot")) {
      return this.json(this.snapshot());
    }

    if (request.method === "POST" && url.pathname.endsWith("/join")) {
      const body = (await request.json()) as RoomJoinRequest;
      return this.registerMember(body);
    }

    if (request.method === "POST" && url.pathname.endsWith("/leave")) {
      const body = (await request.json()) as Pick<RoomJoinRequest, "client_id">;
      return this.unregisterMember(body.client_id);
    }

    return new Response("Not found", { status: 404 });
  }

  private registerMember(body: RoomJoinRequest): Response {
    if (this.currentSessionId && this.currentSessionId !== body.session_id) {
      return new Response("Room already bound to another session", {
        status: 409,
      });
    }

    this.currentSessionId = body.session_id;
    this.members.set(body.client_id, {
      client_id: body.client_id,
      participant_id: body.participant_id,
      role: body.role,
      joined_at: new Date().toISOString(),
    });

    return this.json({
      ok: true,
      snapshot: this.snapshot(),
    });
  }

  private unregisterMember(clientId: string): Response {
    this.members.delete(clientId);
    if (this.members.size === 0) {
      this.currentSessionId = null;
    }

    return this.json({
      ok: true,
      snapshot: this.snapshot(),
    });
  }

  private snapshot(): RoomSnapshot {
    return {
      session_id: this.currentSessionId,
      room_id: this.roomId,
      member_count: this.members.size,
      members: [...this.members.values()],
      updated_at: new Date().toISOString(),
    };
  }

  private json(value: RoomSnapshot | RoomActionResponse): Response {
    return new Response(JSON.stringify(value), {
      headers: {
        "content-type": "application/json; charset=utf-8",
      },
    });
  }
}
